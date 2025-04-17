import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { AuthService } from '../services/auth.service';
import { GetItemsService } from '../services/get-items.service';
import { ItemData } from '../item-data';
import { AdminItemComponent } from '../admin-item/admin-item.component';
import { MatDialog } from '@angular/material/dialog';
import { UpdateItemService } from '../services/update-item.service'; // Adjust the path accordingly
import { AdminPopupComponent } from '../admin-popup/admin-popup.component';
import { Subscription } from 'rxjs';

@Component({
  selector: 'app-admin',
  templateUrl: './admin.component.html',
  styleUrl: './admin.component.css',
})
export class AdminComponent {
  constructor(
    private authService: AuthService,
    private router: Router,
    private getItemsService: GetItemsService,
    private dialog: MatDialog,
    private updateItemService: UpdateItemService,
  ) {}
  items: ItemData[] = [];
  isPopupVisible = false;
  signal: any;
  private sub!: Subscription;
  selectedItem: ItemData = {
    id: 0,
    name: '',
    size: '',
    is_metric: 'True',
    loc_shelf: '',
    loc_rack: '',
    loc_box: '',
    loc_row: '',
    loc_col: '',
    loc_depth: '',
    count: 0,
    threshold: 0,
  };
  toChange = 0;
  ngOnInit(): void {
    this.authService.isAuthenticated().subscribe((isAuth: boolean) => {
      if (!isAuth) {
        this.router.navigate(['/authentication']);
        return;
      }

      this.loadItems(); // Separate method to keep it clean

      this.sub = this.updateItemService.signal$.subscribe((data: any) => {
        this.signal = data;
        this.loadItems(); // Reuse item-fetching logic
      });
    });
  }

  loadItems(): void {
    this.getItemsService.getAllItems().subscribe({
      next: (response: any) => {
        console.log(response);
        this.items = response.data;
      },
      error: (err: any) => {
        console.error('Error fetching items:', err);
      },
    });
  }
  trackByItemId(index: number, item: ItemData): number {
    return item.id; // Assuming 'id' is the unique identifier for each item
  }

  ngOnDestroy() {
    this.sub?.unsubscribe();
  }
  singleSearch(data: any) {
    this.getItemsService.getItem(data.name, data.metric, data.size).subscribe({
      next: (response: any) => {
        this.items = response.data; // Extract 'data' from response
      },
      error: (err: any) => {
        console.error('Error fetching item:', err);
      },
    });
  }
  multiSearch(data: any) {
    this.getItemsService
      .getFuzzyItems(data.name, data.metric, data.size)
      .subscribe({
        next: (response: any) => {
          this.items = response.data; // Extract 'data' from response
        },
        error: (err: any) => {
          console.error('Error fetching item:', err);
        },
      });
  }

  handleSearch(event: { data: any; action: string }) {
    var action = event.action;
    var data = event.data;
    switch (action) {
      case 'single':
        this.singleSearch(data);
        break;
      case 'multi':
        this.multiSearch(data);
        break;
    }
  }
  addItem(event: any) {
    this.authService.levelGetter().subscribe((level) => {
      if (level < 2) {
        const PopUp = this.dialog.open(AdminPopupComponent);
        PopUp.componentInstance.showAddItemPopup();
      }
    });
  }

  check_level() {
    const level = this.authService.levelGetter().subscribe((level) => {
      if (level != 2) return true;
      else return false;
    });
  }
  closePopup() {
    this.isPopupVisible = false;
    this.getItemsService.getAllItems().subscribe({
      next: (response) => {
        this.items = response.data;
      },
    });
  }
  onItemClick(item: any) {
    this.selectedItem = item;
    const PopUp = this.dialog.open(AdminPopupComponent);
    PopUp.componentInstance.showItem(this.selectedItem);
  }
  incrementItem(event: Event, item: any) {
    event.stopPropagation();
    this.updateItemService
      .incrementItem(item, this.toChange)
      .subscribe((response) => {
        if (response.error) {
          console.error(response.error);
        } else {
          item.count += this.toChange;
        }
      });
  }
  decrementItem(event: Event, item: any) {
    event.stopPropagation();
    this.updateItemService
      .decrementItem(item, this.toChange)
      .subscribe((response) => {
        if (response.error) {
          console.error(response.error);
        } else {
          item.count -= this.toChange;
        }
      });
  }
}

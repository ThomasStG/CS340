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
  items: ItemData[] = []; // the list of items
  isPopupVisible = false; // flag to determine if the popup is visible
  signal: any; // variable to hold the signal sent by updateItemService
  private sub!: Subscription; // variable to hold the subscription
  selectedItem: ItemData = {
    // variable to hold the selected item
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
  toChange = 0; // variable to hold the number of items to add or remove
  ngOnInit(): void {
    /*
     * Runs on component initialization. Checks if the user is authenticated, if not, navigates to the authentication page,
     * otherwise load the item list and subscribe to a signal to refresh items on update.
     *
     * Args:
     *   None
     *
     * Returns:
     *   None
     */
    this.authService.isAuthenticated().subscribe((isAuth: boolean) => {
      if (!isAuth) {
        this.router.navigate(['/authentication']);
        return;
      }

      this.loadItems();

      this.sub = this.updateItemService.signal$.subscribe((data: any) => {
        this.signal = data;
        this.loadItems();
      });
    });
  }

  loadItems(): void {
    /*
     * Fetches the list of items from the server and updates the items array.
     *
     * Args:
     *   None
     *
     * Returns:
     *   None
     */
    this.getItemsService.getAllItems().subscribe({
      next: (response: any) => {
        this.items = response.data;
      },
      error: (err: any) => {
        console.error('Error fetching items:', err);
      },
    });
  }
  trackByItemId(index: number, item: ItemData): number {
    /*
     * Returns the unique identifier for each item in the list.
     *
     * Args:
     *   index: The index of the item in the list.
     *   item: The item object.
     *
     * Returns:
     *   The unique identifier for the item.
     */
    return item.id; // Assuming 'id' is the unique identifier for each item
  }

  ngOnDestroy() {
    /*
     * Unsubscribes from the subscription when the component is destroyed.
     *
     * Args:
     *   None
     *
     * Returns:
     *   None
     */
    this.sub?.unsubscribe();
  }

  singleSearch(data: any) {
    /*
     * Fetches a single item from the server based on the provided data.
     *
     * Args:
     *   data: The ItemData object containing the item information.
     *
     * Returns:
     *   None
     */
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
    /*
     * Fetches multiple items from the server based on the provided data.
     *
     * Args:
     *   data: The ItemData object containing the item information.
     *
     * Returns:
     *   None
     */
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
    /*
     * Handles the search event and fetches items based on the provided data.
     *
     * Args:
     *   event: The event object containing the search data and action.
     *
     * Returns:
     *   None
     */
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
    /*
     * Opens the admin popup to add a new item.
     *
     * Args:
     *   event: The event object.
     *
     * Returns:
     *   None
     */
    this.authService.levelGetter().subscribe((level) => {
      if (level < 2) {
        const PopUp = this.dialog.open(AdminPopupComponent);
        PopUp.componentInstance.showAddItemPopup();
      }
    });
  }

  check_level() {
    /*
     * Checks if the user's authentication level is not 2 (generic student worker).
     *
     * Args:
     *   None
     *
     * Returns:
     *   True if the user's authentication level is not 2, false otherwise.
     */
    const level = this.authService.levelGetter().subscribe((level) => {
      if (level != 2) return true;
      else return false;
    });
  }

  closePopup() {
    /*
     * Closes the admin popup and reloads the items.
     *
     * Args:
     *   None
     *
     * Returns:
     *   None
     */
    this.isPopupVisible = false;
    this.getItemsService.getAllItems().subscribe({
      next: (response) => {
        this.items = response.data;
      },
    });
  }

  onItemClick(item: any) {
    /*
     * Opens the admin popup to edit an item.
     *
     * Args:
     *   item: The item object.
     *
     * Returns:
     *   None
     */
    this.selectedItem = item;
    const PopUp = this.dialog.open(AdminPopupComponent);
    PopUp.componentInstance.showItem(this.selectedItem);
  }

  incrementItem(event: Event, item: any) {
    /*
     * Increments the count of an item.
     *
     * Args:
     *   event: The event object.
     *   item: The item object.
     *
     * Returns:
     *   None
     */
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
    /*
     * Decrements the count of an item.
     *
     * Args:
     *   event: The event object.
     *   item: The item object.
     *
     * Returns:
     *   None
     */
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

import { Component } from '@angular/core';
import { ItemSearchComponent } from '../item-search/item-search.component';
import { ItemData } from '../item-data';
import { GetItemsService } from '../services/get-items.service';
import { ItemPopupComponent } from '../item-popup/item-popup.component';
import { MatDialog } from '@angular/material/dialog';
import { FormGroup, FormControl, Validators } from '@angular/forms';

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrl: './home.component.css',
})
export class HomeComponent {
  items: ItemData[] = [];
  constructor(
    private getItemsService: GetItemsService,
    private dialog: MatDialog,
  ) {}
  isPopupVisible = false;
  searchForm = new FormGroup({
    name: new FormControl('', Validators.required),
    size: new FormControl('', Validators.required),
    metric: new FormControl('True'), // Default value
  });
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

  singleSearch(data: any) {
    this.getItemsService.getItem(data.name, data.metric, data.size).subscribe({
      next: (response) => {
        this.items = response.data; // Extract 'data' from response
      },
      error: (err) => {
        console.error('Error fetching item:', err);
      },
    });
  }
  multiSearch(data: any) {
    this.getItemsService
      .getFuzzyItems(data.name, data.metric, data.size)
      .subscribe({
        next: (response) => {
          this.items = response.data; // Extract 'data' from response
        },
        error: (err) => {
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

  ngOnInit(): void {
    this.getItemsService.getAllItems().subscribe({
      next: (response) => {
        console.log(response.data);
        this.items = response.data; // Extract 'data' from response
      },
      error: (err) => {
        console.error('Error fetching item:', err);
      },
    });
  }
  onItemClick(item: any) {
    this.selectedItem = item;
    const PopUp = this.dialog.open(ItemPopupComponent);
    PopUp.componentInstance.showItem(this.selectedItem);
  }

  // Close popup
  closePopup() {
    this.isPopupVisible = false;
  }
}

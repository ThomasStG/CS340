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
      next: (response) => {
        this.items = response.data; // Extract 'data' from response
      },
      error: (err) => {
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
        next: (response) => {
          this.items = response.data; // Extract 'data' from response
        },
        error: (err) => {
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

  ngOnInit(): void {
    /*
     * Loades the item list
     *
     * Args:
     *   None
     *
     * Returns:
     *   None
     */
    this.loadItems();
  }
  onItemClick(item: any) {
    /*
     * Opens a item popup with sending the items data
     *
     * Args:
     *   Selected items data
     *
     * Returns:
     *   None
     */
    this.selectedItem = item;
    const PopUp = this.dialog.open(ItemPopupComponent);
    PopUp.componentInstance.showItem(this.selectedItem);
  }

  // Close popup
  closePopup() {
    /*
     * Sets the visibility variable to false
     *
     * Args:
     *   None
     *
     * Returns:
     *   None
     */
    this.isPopupVisible = false;
  }

  loadItems(): void {
    /*
     * Call getAllItems from the get item service and loads them all to the screen.
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
}

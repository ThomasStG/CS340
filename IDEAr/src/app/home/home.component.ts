import { Component } from '@angular/core';
import { ItemSearchComponent } from '../item-search/item-search.component';
import { ItemData } from '../item-data';
import { GetItemsService } from '../services/get-items.service';

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrl: './home.component.css',
})
export class HomeComponent {
  items: ItemData[] = [];
  constructor(private getItemsService: GetItemsService) {}

  trackBySize(index: number, item: any) {
    return item.size;
  }

  /* incrementCount(item: any) {
    if (!this.itemInput[item.name]) {
      this.itemInput[item.name] = 1;
    }
    item.count += this.itemInput[item.name];
  }

  decrementCount(item: any) {
    if (!this.itemInput[item.name]) {
      this.itemInput[item.name] = 1;
    }
    item.count -= this.itemInput[item.name];
  }

  getName(event: any) {
    alert(`Item Name: ${event.target.id}`);
  } */
  singleSearch(data: any) {
    this.getItemsService.getItem(data.name, data.metric, data.size).subscribe({
      next: (response) => {
        console.log('API Response:', response);
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
          console.log('API Response:', response);

          console.log(response.data);
          this.items = response.data; // Extract 'data' from response
          console.log(this.items);
        },
        error: (err) => {
          console.error('Error fetching item:', err);
        },
      });
  }

  handleSearch(event: { data: any; action: string }) {
    var action = event.action;
    var data = event.data;
    console.log(data);
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
        console.log('API Response:', response);
        this.items = response.data; // Extract 'data' from response
      },
      error: (err) => {
        console.error('Error fetching item:', err);
      },
    });
  }
}

import { Component } from '@angular/core';
import { ItemData } from './item-data';
import { GetItemsService } from './get-items.service';
@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrl: './app.component.css',
})
export class AppComponent {
  title = 'IDEAr';
  items: ItemData[] = [];

  constructor(private getItemsService: GetItemsService) {}

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

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

  ngOnInit(): void {
    this.getItemsService.getData('Plastic Screws', false, '8/32').subscribe({
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

import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { AuthService } from '../auth.service';
import { GetItemsService } from '../get-items.service';
import { ItemData } from '../item-data';
import { AdminItemComponent } from '../admin-item/admin-item.component';

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
  ) {}
  items: ItemData[] = [];
  ngOnInit(): void {
    this.authService.isAuthenticated().subscribe((isAuth) => {
      if (!isAuth) {
       // this.router.navigate(['/authentication']);
      //} else {
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
    });
  }
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
}

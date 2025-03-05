import { Component } from '@angular/core';

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrl: './home.component.css'
})
export class HomeComponent {
  // Move these from AppComponent
  Name: string = '';
  Size: string = '';
  isMetric: boolean = false;
  testList: any[] = [
    { name: 'Item 1', size: 'Small', ismetric: true, location: 'A1', count: 5, threshold: 10 },
    { name: 'Item 2', size: 'Large', ismetric: false, location: 'B2', count: 3, threshold: 7 }
  ];
  itemInput: { [key: string]: number } = {};

  trackBySize(index: number, item: any) {
    return item.size;
  }

  incrementCount(item: any) {
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
  }


}

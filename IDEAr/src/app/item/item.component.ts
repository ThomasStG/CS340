import { Component, Input, OnInit } from '@angular/core';
import { ItemData } from '../item-data';

@Component({
  selector: 'app-item',
  templateUrl: './item.component.html',
  styleUrl: './item.component.css',
  host: { ngSkipHydration: 'true' },
})
export class ItemComponent implements OnInit {
  @Input() item: ItemData = {
    id: 0,
    name: '',
    size: '',
    is_metric: 'True',
    location: '',
    count: 0,
    threshold: 0,
  };
  ngOnInit() {
    console.log('Type of location:', typeof this.item.location);

    if (this.item && this.item.location) {
      console.log('Before parsing:', this.item.location);

      // Check if the location is a string before parsing
      if (typeof this.item.location === 'string') {
        try {
          this.item.location = JSON.parse(this.item.location);
          console.log('After parsing:', this.item.location);
        } catch (error) {
          console.error('Error parsing location:', error);
        }
      } else {
        console.log('No need to parse, location is already an object/array.');
      }
    } else {
      console.error('Item or location is not defined.');
    }
  }
}

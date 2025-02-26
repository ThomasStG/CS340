import { Component, Input } from '@angular/core';
import { ItemData } from '../item-data';

@Component({
  selector: 'app-item',
  templateUrl: './item.component.html',
  styleUrl: './item.component.css',
})
export class ItemComponent {
  @Input() item: ItemData = {
    name: '',
    size: '',
    metric: false,
    location: '',
    count: 0,
    threshold: 0,
  };
}

import { Component, Input, OnInit } from '@angular/core';
import { ItemData } from '../item-data';

@Component({
  selector: 'app-item',
  templateUrl: './item.component.html',
  styleUrl: './item.component.css',
})
export class ItemComponent implements OnInit {
  @Input() item: ItemData = {
    name: '',
    size: '',
    metric: true,
    location: '',
    count: 0,
    threshold: 0,
  };
  ngOnInit() {
    this.item.metric = this.normalizeMetric(this.item.metric);
  }

  normalizeMetric(value: any): boolean {
    return value === 'True' || value === 1 || value === true; // Normalize to boolean
  }
}

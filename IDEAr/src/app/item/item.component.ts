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
    is_metric: 'True',
    location: '',
    count: 0,
    threshold: 0,
  };
  ngOnInit() {
    console.log(this.item);
    this.item.location = JSON.parse(this.item.location);
    console.log(this.item);
  }
}

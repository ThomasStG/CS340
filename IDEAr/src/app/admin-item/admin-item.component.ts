import { Component, Input, OnInit } from '@angular/core';
import { ItemData } from '../item-data';

@Component({
  selector: 'app-admin-item',
  templateUrl: './admin-item.component.html',
  styleUrl: './admin-item.component.css',
})
export class AdminItemComponent implements OnInit {
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

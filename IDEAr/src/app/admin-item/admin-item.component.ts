import { Component, Input, OnInit } from '@angular/core';
import { ItemData } from '../item-data';
import { UpdateItemService } from '../update-item.service';

@Component({
  selector: 'app-admin-item',
  templateUrl: './admin-item.component.html',
  styleUrl: './admin-item.component.css',
})
export class AdminItemComponent implements OnInit {
  // constructor() {
  //   private updateService = new UpdateItemService();
  // }
  @Input() item: ItemData = {
    id: 0,
    name: '',
    size: '',
    is_metric: 'True',
    location: '',
    count: 0,
    threshold: 0,
  };
  // isPopupVisible = false;
  // oldItem: ItemData;
  ngOnInit() {
    this.item.location = JSON.parse(this.item.location);
    // oldItem = { ...this.item };
  }

  // isPopupVisible = false;

  // showPopup() {
  //   this.isPopupVisible = true;
  // }

  // closePopup(event: Event) {
  //   event.stopPropagation();
  //   this.isPopupVisible = false;
  // }
  // updateItem(event: Event) {
  //   event.stopPropagation();
  //   this.isPopupVisible = false;
  //   this.updateService.updateItem(this.item, this.oldItem);
  // }
}

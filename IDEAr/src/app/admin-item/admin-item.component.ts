import { Component, Input, OnInit } from '@angular/core';
import { ItemData } from '../item-data';
import { UpdateService } from '../update-item.service';

@Component({
  selector: 'app-admin-item',
  templateUrl: './admin-item.component.html',
  styleUrl: './admin-item.component.css',
})
export class AdminItemComponent implements OnInit {
  constructor() {
    updateService = new UpdateService();
  }
  @Input() item: ItemData = {
    id: 0,
    name: '',
    size: '',
    is_metric: 'True',
    location: '',
    count: 0,
    threshold: 0,
  };
  oldItem: ItemData = { ...this.item };
  ngOnInit() {
    this.item.location = JSON.parse(this.item.location);
  }

  @Input() itemPopup: any; // The item passed to this component
  isPopupVisible = false;

  showPopup() {
    this.isPopupVisible = true;
  }

  closePopup(event: Event) {
    event.stopPropagation();
    this.isPopupVisible = false;
  }
  updateItem(event: Event) {
    event.stopPropagation();
    this.isPopupVisible = false;
    this.updateService.updateItem(this.item, this.oldItem);
  }
}

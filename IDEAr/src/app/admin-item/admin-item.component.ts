import { Component, Input, OnInit } from '@angular/core';
import { ItemData } from '../item-data';
import { UpdateItemService } from '../services/update-item.service';

@Component({
  selector: 'app-admin-item',
  templateUrl: './admin-item.component.html',
  styleUrl: './admin-item.component.css',
})
export class AdminItemComponent implements OnInit {
  constructor(private updateItemService: UpdateItemService) {}
  @Input() item: ItemData = {
    id: 0,
    name: '',
    size: '',
    is_metric: 'True',
    location: '',
    count: 0,
    threshold: 0,
  };
  newItem: ItemData = { ...this.item };
  changeNum = 0;
  ngOnInit() {
    this.item.location = JSON.parse(this.item.location);
    this.newItem = this.item;
  }

  isPopupVisible = false;
  isEditing = false;

  editItem(event: Event) {
    event.stopPropagation();
    this.isEditing = true;
  }
  cancelEditing(event: Event) {
    event.stopPropagation();
    this.isEditing = false;
  }

  showPopup() {
    this.isPopupVisible = true;
  }

  closePopup(event: Event) {
    event.stopPropagation();
    this.isPopupVisible = false;
    this.isEditing = false;
  }
  updateItem(event: Event) {
    event.stopPropagation();
    this.isEditing = false;
    this.isPopupVisible = false;
    this.updateItemService
      .updateItem(this.item, this.newItem)
      .subscribe((response) => {
        console.log(response);
      });
  }
  deleteItem(event: Event) {
    event.stopPropagation();
    this.updateItemService.deleteItem(this.item).subscribe((response) => {
      console.log(response);
    });
  }
  incrementItem(event: Event) {
    event.stopPropagation();
    this.updateItemService
      .incrementItem(this.item, this.changeNum)
      .subscribe((response) => {
        if (response.error) {
          console.error(response.error);
        } else {
          this.item.count += this.changeNum;
        }
      });
  }
  decrementItem(event: Event) {
    event.stopPropagation();
    this.updateItemService
      .decrementItem(this.item, this.changeNum)
      .subscribe((response) => {
        if (response.error) {
          console.error(response.error);
        } else {
          this.item.count -= this.changeNum;
        }
      });
  }
}

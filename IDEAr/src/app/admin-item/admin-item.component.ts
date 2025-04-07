import { Component, Input, OnInit } from '@angular/core';
import { ItemData } from '../item-data';
import { UpdateItemService } from '../update-item.service';
import { AuthService } from '../auth.service';

@Component({
  selector: 'app-admin-item',
  templateUrl: './admin-item.component.html',
  styleUrl: './admin-item.component.css',
})
export class AdminItemComponent implements OnInit {
  constructor(
    private updateItemService: UpdateItemService,
    private authService: AuthService,
  ) {}
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
  toChange = 0;
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
      .updateItem(this.item, this.newItem, this.authService.getToken())
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
      .incrementItem(this.item, this.toChange)
      .subscribe((response) => {
        if (response.error) {
          console.error(response.error);
        } else {
          this.item.count += this.toChange;
        }
      });
  }
  decrementItem(event: Event) {
    event.stopPropagation();
    this.updateItemService
      .decrementItem(this.item, this.toChange)
      .subscribe((response) => {
        if (response.error) {
          console.error(response.error);
        } else {
          this.item.count -= this.toChange;
        }
      });
  }
}

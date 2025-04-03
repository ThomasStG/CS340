import { Component } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';
import { ItemData } from '../item-data';
import { UpdateItemService } from '../update-item.service';

@Component({
  selector: 'app-admin-popup',
  templateUrl: './admin-popup.component.html',
  styleUrl: './admin-popup.component.css',
})
export class AdminPopupComponent {
  item: ItemData = {
    id: 0,
    name: '',
    size: '',
    is_metric: 'True',
    location: '',
    count: 0,
    threshold: 0,
  };
  constructor(
    public dialog: MatDialog,
    private updateItemService: UpdateItemService,
  ) {}
  close() {
    this.dialog.closeAll();
  }
  save() {
    this.updateItemService.addItem(this.item).subscribe((response) => {
      if (response.error) {
        console.error(response.error);
      }
    });
    this.close();
  }
}

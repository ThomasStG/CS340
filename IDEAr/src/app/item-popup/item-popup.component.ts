import { Component } from '@angular/core';
import { Input, Output, EventEmitter } from '@angular/core';
import { MatDialogRef } from '@angular/material/dialog';
import { UtilityService } from '../services/utility.service';
import { BehaviorSubject } from 'rxjs';
import { ItemData } from '../item-data';

@Component({
  selector: 'app-item-popup',
  templateUrl: './item-popup.component.html',
  styleUrl: './item-popup.component.css',
})
export class ItemPopupComponent {
  @Input() item: ItemData = {
    id: 0,
    name: '',
    size: '',
    is_metric: 'True',
    loc_shelf: '',
    loc_rack: '',
    loc_box: '',
    loc_row: '',
    loc_col: '',
    loc_depth: '',
    count: 0,
    threshold: 0,
  };

  darkMode = new BehaviorSubject<boolean>(false);

  constructor(
    private dialogRef: MatDialogRef<ItemPopupComponent>,
    private utilityService: UtilityService,
  ) {}
  newItem: ItemData = { ...this.item };
  ngOnInit() {
    this.darkMode.next(this.utilityService.isDarkMode());
    console.log(this.item);
  }

  showItem(item: ItemData) {
    this.item = item;
  }

  stopClickPropagation(event: Event) {
    event.stopPropagation();
  }

  closePopup(event: Event) {
    event.stopPropagation();
    this.dialogRef.close();
  }

  @Output() close = new EventEmitter<void>();
}

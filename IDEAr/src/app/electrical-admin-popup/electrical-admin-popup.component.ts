import { Component } from '@angular/core';
import { Input, Output, EventEmitter } from '@angular/core';
import { MatDialogRef } from '@angular/material/dialog';
import { UtilityService } from '../services/utility.service';
import { BehaviorSubject } from 'rxjs';

import { ElectricalItemData } from '../electrical-item-data';
import { ElectricalUpdateService } from '../services/electrical-update.service';

@Component({
  selector: 'app-electrical-admin-popup',
  templateUrl: './electrical-admin-popup.component.html',
  styleUrl: './electrical-admin-popup.component.css',
})
export class ElectricalAdminPopupComponent {
  @Input() item: ElectricalItemData = {
    type: '',
    name: '',
    part_id: 0,
    id: 0,
    subtype: '',
    value: 0,
    count: 0,
    location: 'EL',
    rack: 0,
    slot: '',
    max_v: 0,
    max_p: 0,
    max_i: 0,
    i_hold: 0,
    description: '',
    part_number: '',
    link: '',
    tolerance: 0,
    seller: '',
    dielectric_material: '',
    mounting_method: '',
    polarity: false,
    is_assembly: false,
  };

  darkMode = new BehaviorSubject<boolean>(false);

  isEditing = false;
  isAdding = false;

  constructor(
    private dialogRef: MatDialogRef<ElectricalAdminPopupComponent>,
    private electricalUpdateService: ElectricalUpdateService,
    private utilityService: UtilityService,
  ) {}
  newItem: any = { ...this.item };
  ngOnInit() {
    this.darkMode.next(this.utilityService.isDarkMode());
    console.log(this.item);
    this.newItem = { ...this.item };
  }

  showItem(item: any) {
    this.item = item;
  }

  editItem(event: Event) {
    this.isEditing = true;
  }

  saveItem(event: Event) {
    this.isEditing = false;
    this.electricalUpdateService
      .updateItem(this.newItem, this.item)
      .subscribe(() => {});
    this.closePopup(event, 'edit');
  }

  addItem(event: Event) {
    this.electricalUpdateService.addItem(this.item).subscribe(() => {});
    this.closePopup(event);
  }

  deleteItem(event: Event) {
    this.electricalUpdateService.deleteItem(this.item).subscribe(() => {});
    this.closePopup(event, 'delete');
  }

  stopClickPropagation(event: Event) {
    event.stopPropagation();
  }
  cancel(event: Event) {
    this.isEditing = false;
    this.newItem = { ...this.item };
    this.closePopup(event);
  }

  closePopup(event: Event, type?: string) {
    event.stopPropagation();
    console.log(this.newItem);
    this.close.emit([type, this.newItem]);
    this.dialogRef.close();
  }

  @Output() close = new EventEmitter<any>();

  showAddItemPopup() {
    this.isEditing = true;
    this.isAdding = true;
  }
}

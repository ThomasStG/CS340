import { Component } from '@angular/core';
import { Input, Output, EventEmitter } from '@angular/core';
import { MatDialogRef } from '@angular/material/dialog';
import { UtilityService } from '../services/utility.service';
import { BehaviorSubject } from 'rxjs';

import { ElectricalItemData } from '../electrical-item-data';

@Component({
  selector: 'app-electrical-item-popup',
  templateUrl: './electrical-item-popup.component.html',
  styleUrl: './electrical-item-popup.component.css',
})
export class ElectricalItemPopupComponent {
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

  constructor(
    private dialogRef: MatDialogRef<ElectricalItemPopupComponent>,
    private utilityService: UtilityService,
  ) {}
  newItem: ElectricalItemData = { ...this.item };
  ngOnInit() {
    this.darkMode.next(this.utilityService.isDarkMode());
  }

  showItem(item: any) {
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

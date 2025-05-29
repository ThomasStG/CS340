import { Component } from '@angular/core';
import { MatDialog } from '@angular/material/dialog';

import { ElectricalSearchService } from '../services/electrical-search.service';
import { ElectricalItemPopupComponent } from '../electrical-item-popup/electrical-item-popup.component';

import { UtilityService } from '../services/utility.service';

@Component({
  selector: 'app-electrical-home',
  templateUrl: './electrical-home.component.html',
  styleUrl: './electrical-home.component.css',
})
export class ElectricalHomeComponent {
  searched: boolean = false;
  items: any[] = [];
  type?: string = '';
  unit?: string = '';
  subtype?: string = '';

  isPopupVisible: boolean = false;
  selectedItem: any = null;

  helpText: string = '';

  constructor(
    private electricalSearchService: ElectricalSearchService,
    private dialog: MatDialog,
    private utilityService: UtilityService,
  ) {}

  ngOnInit() {
    this.utilityService
      .getElectricalTooltip()
      .subscribe((data) => (this.helpText = data));
  }

  onSearch(event: {
    items: any[];
    subtype?: string;
    type?: string;
    unit?: string;
    multiplier?: number;
  }) {
    this.items = event.items;
    this.searched = true;
    this.type = event.type;
    switch (this.type) {
      case 'passive':
        this.unit = event.unit;
        this.subtype = event.subtype;
        if (event.multiplier) {
          for (let i = 0; i < this.items.length; i++) {
            this.items[i].value = this.items[i].value / event.multiplier;
          }
        }
        break;
      case 'assembly':
        this.subtype = event.subtype;
        break;
      case 'active':
        this.items = event.items;
        break;
    }
  }

  onItemClick(item: any) {
    this.selectedItem = item;
    const PopUp = this.dialog.open(ElectricalItemPopupComponent);
    PopUp.componentInstance.showItem(this.selectedItem);
  }

  closePopup() {
    this.isPopupVisible = false;
  }
  onClear(event: any) {
    this.searched = false;
    this.items = [];
  }
}

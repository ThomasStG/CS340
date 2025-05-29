import { Component } from '@angular/core';
import { ElectricalSearchService } from '../services/electrical-search.service';
import { UtilityService } from '../services/utility.service';
import { MatDialog } from '@angular/material/dialog';
import { ElectricalAdminPopupComponent } from '../electrical-admin-popup/electrical-admin-popup.component';
import { ElectricalUpdateService } from '../services/electrical-update.service';

@Component({
  selector: 'app-electrical-admin',
  templateUrl: './electrical-admin.component.html',
  styleUrl: './electrical-admin.component.css',
})
export class ElectricalAdminComponent {
  searched: boolean = false;
  items: any[] = [];
  type: string = '';
  unit: string = '';
  subtype: string = '';

  amount: number = 0;

  isPopupVisible: boolean = false;
  selectedItem: any = null;

  helpText: string = '';
  editingText: boolean = false;

  constructor(
    private electricalSearchService: ElectricalSearchService,
    private dialog: MatDialog,
    private utilityService: UtilityService,
    private electricalUpdateService: ElectricalUpdateService,
  ) {}

  ngOnInit() {
    this.utilityService
      .getElectricalTooltip()
      .subscribe((data) => (this.helpText = data));
  }

  editText() {
    this.editingText = true;
  }
  saveText() {
    console.log(this.helpText);
    this.utilityService
      .setElectricalTooltip(this.helpText)
      .subscribe((_) => console.log('Tooltip updated'));
    this.editingText = false;
  }
  cancelText() {
    this.utilityService
      .getElectricalTooltip()
      .subscribe((data) => (this.helpText = data));
    this.editingText = false;
  }

  onSearch(event: {
    items: any[];
    type: string;
    subtype?: string;
    unit?: string;
    multiplier?: number;
  }) {
    console.log(event);
    this.items = event.items;
    this.searched = true;
    this.type = event.type;
    console.log(this.type);
    for (let i = 0; i < this.items.length; i++) {
      console.log(this.items[i].type);
    }
    if (event.unit) {
      this.unit = event.unit;
    }
    if (event.subtype) {
      this.subtype = event.subtype;
    }
    if (event.multiplier) {
      const multiplier = event.multiplier;
      for (let i = 0; i < this.items.length; i++) {
        this.items[i].value = this.items[i].value / multiplier;
      }
    }
    console.log(this.items);
  }

  onItemClick(item: any) {
    console.log('item clicked');
    this.selectedItem = item;
    const PopUp = this.dialog.open(ElectricalAdminPopupComponent);
    PopUp.componentInstance.showItem(this.selectedItem);
  }

  closePopup(event: { item: any; type: string } | any) {
    console.log('event', event);
    const type = event?.type;
    this.isPopupVisible = false;
    const item = event?.item;

    const index = this.items.findIndex(
      (el) => el.id === item.id || el.part_id === item.part_id,
    );

    if (type === 'edit' && index !== -1) {
      // Update the item in place
      this.items[index] = item;
    } else if (type === 'delete' && index !== -1) {
      console.log(index);
      // Remove the item
      this.items.splice(index, 1);
    }
  }
  onClear(event: any) {
    this.searched = false;
    this.items = [];
  }
  increment(item: any, event: any) {
    event.stopPropagation();
    const temp = item;
    item.count += this.amount;
    this.electricalUpdateService.updateItem(temp, item).subscribe(() => {});
  }
  decrement(item: any, event: any) {
    event.stopPropagation();
    if (item.count > 0) {
      const temp = item;
      item.count -= this.amount;
      this.electricalUpdateService.updateItem(temp, item).subscribe(() => {});
    }
  }
}

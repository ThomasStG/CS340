import { Component } from '@angular/core';
import { Input, Output, EventEmitter } from '@angular/core';

@Component({
  selector: 'app-item-popup',
  templateUrl: './item-popup.component.html',
  styleUrl: './item-popup.component.css',
})
export class ItemPopupComponent {
  @Input() item: any;
  @Output() close = new EventEmitter<void>();

  closePopup() {
    this.close.emit();
  }
}

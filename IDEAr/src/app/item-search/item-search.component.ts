import { FormGroup, FormControl, Validators } from '@angular/forms';
import { Component, EventEmitter, Output } from '@angular/core';

@Component({
  selector: 'app-item-search',
  templateUrl: './item-search.component.html',
  styleUrl: './item-search.component.css',
})
export class ItemSearchComponent {
  @Output() formSubmit = new EventEmitter<any>();
  searchForm = new FormGroup({
    name: new FormControl('', Validators.required),
    size: new FormControl('', Validators.required),
    metric: new FormControl('True'), // Default value
  });

  onSubmit(action: string) {
    if (this.searchForm.valid) {
      this.formSubmit.emit({ data: this.searchForm.value, action });
    }
  }
}

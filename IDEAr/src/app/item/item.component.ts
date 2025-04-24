import { Component, Input, OnInit } from '@angular/core';
import { ItemData } from '../item-data';

@Component({
  selector: 'app-item',
  templateUrl: './item.component.html',
  styleUrl: './item.component.css',
  host: { ngSkipHydration: 'true' },
})
export class ItemComponent  {
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
  // The item data to be displayed in the component
  // id
  // name
  // size
  // is_metric: whether the item is in metric or imperial units
  // loc_shelf: the shelf location of the item
  // loc_rack: the rack location of the item
  // loc_box: the box location of the item
  // loc_row: the row location of the item
  // loc_col: the column location of the item
  // loc_depth: the depth location of the item
  // count: the quantity of the item
  // threshold: the threshold quantity for the item

  
}
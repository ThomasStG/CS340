import { Injectable } from '@angular/core';

import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root',
})
export class ElectricalUpdateService {
  constructor(private http: HttpClient) {}

  addItem(item: any): Observable<any> {
    return this.http.post('http://127.0.0.1:3000/electricalAddItem', item);
  }

  updateItem(item: any, old_item: any): Observable<any> {
    console.log(item.subtype);
    console.log(item.max_p);
    const body: any = {
      item_id: item.id,
      name: old_item.name,
      part_id: old_item.part_id,
      count: item.count,
      location: item.location,
      rack: item.rack,
      slot: item.slot,
      type: item.type,
      max_v: item.max_v,
      max_p: item.max_p,
      max_i: item.max_i,
      i_hold: item.i_hold,
      subtype: item.subtype,
      value: item.value,
      description: item.description,
      part_number: item.part_number,
      link: item.link,
      new_name: item.name,
      new_part_id: item.part_id,
      tolerance: item.tolerance,
      seller: item.seller,
      dielectric_material: item.dielectric_material,
      mounting_method: item.mounting_method,
      polarity: item.polarity,
      is_assembly: item.is_assembly,
    };
    console.log('body', body);
    return this.http.post('http://127.0.0.1:3000/electricalUpdateItem', body);
  }

  deleteItem(item: any): Observable<any> {
    const body: any = {
      item: item,
    };
    if (item.type === 'passive') {
      return this.http.post(
        'http://127.0.0.1:3000/electricalRemovePassive',
        body,
      );
    } else {
      return this.http.post(
        'http://127.0.0.1:3000/electricalRemoveActive',
        body,
      );
    }
  }
}

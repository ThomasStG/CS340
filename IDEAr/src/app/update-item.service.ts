import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { ItemData } from './item-data';

@Injectable({
  providedIn: 'root',
})
export class UpdateItemService {
  constructor(private http: HttpClient) {}
  updateItem(newItem: ItemData, oldItem: ItemData): Observable<any> {
    var locationJSON = JSON.stringify(newItem.location);
    const url = `http://127.0.0.1:3000/updateitem?
                  name=${encodeURIComponent(oldItem.name)}&
                  new_name=${encodeURIComponent(newItemname)}&
                  isMetric=${oldItem.isMetric}&
                  new_isMetric=${newItem.isMetric}&
                  size=${oldItem.size}&
                  new_size=${newItem.size}&
                  id=${oldItem.id}&
                  count=${newItem.count}&
                  location=${encodeURIComponent(locationJSON)}&
                  threshold=${newItem.threshold}`;
    return this.http.get(url);
  }
}

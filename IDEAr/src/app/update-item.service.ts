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
new_name=${encodeURIComponent(newItem.name)}&
is_metric=${oldItem.is_metric}&
new_is_metric=${newItem.is_metric}&
size=${oldItem.size}&
new_size=${newItem.size}&
id=${oldItem.id}&
count=${newItem.count}&
location=${encodeURIComponent(locationJSON)}&
threshold=${newItem.threshold}`;
    return this.http.get(url);
  }
  deleteItem(item: ItemData): Observable<any> {
    const url = `http://127.0.0.1:3000/deleteitem?id=${item.id}`;
    return this.http.get(url);
  }
  decrementItem(item: ItemData, toChange: number): Observable<any> {
    const url = `http://127.0.0.1:3000/decrement?name=${encodeURIComponent(item.name)}&is_metric=${item.is_metric}&size=${item.size}&num=${toChange}`;
    return this.http.get(url);
  }
  incrementItem(item: ItemData, toChange: number): Observable<any> {
    const url = `http://127.0.0.1:3000/increment?name=${encodeURIComponent(item.name)}&is_metric=${item.is_metric}&size=${item.size}&num=${toChange}`;
    return this.http.get(url);
  }
  addItem(item: ItemData): Observable<any> {
    var locationJSON = JSON.stringify(item.location);
    const url = `http://127.0.0.1:3000/add?
name=${encodeURIComponent(item.name)}&
is_metric=${item.is_metric}&
size=${item.size}&
num=${item.count}&
location=${encodeURIComponent(locationJSON)}&
threshold=${item.threshold}`;
    return this.http.get(url);
  }
}

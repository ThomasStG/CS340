import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { ItemData } from '../item-data';
import { AuthService } from './auth.service';

@Injectable({
  providedIn: 'root',
})
export class UpdateItemService {
  constructor(
    private http: HttpClient,
    private authService: AuthService,
  ) {}
  updateItem(newItem: ItemData, oldItem: ItemData): Observable<any> {
    
    const url = `http://127.0.0.1:3000/updateitem?
name=${encodeURIComponent(oldItem.name)}&
new_name=${encodeURIComponent(newItem.name)}&
is_metric=${oldItem.is_metric}&
new_is_metric=${newItem.is_metric}&
size=${oldItem.size}&
new_size=${newItem.size}&
id=${oldItem.id}&
loc_shelf=${newItem.loc_shelf}&
loc_rack=${newItem.loc_rack}&
loc_box=${newItem.loc_box}&
loc_row=${newItem.loc_row}&
loc_col=${newItem.loc_col}&
loc_depth=${newItem.loc_depth}&
count=${newItem.count}&
threshold=${newItem.threshold}&
token=${this.authService.getToken()}`;
    return this.http.get(url);
  }
  deleteItem(item: ItemData): Observable<any> {
    const url = `http://127.0.0.1:3000/deleteitem?id=${item.id}`;
    return this.http.get(url);
  }
  addItem(item: ItemData): Observable<any> {
    
    const url = `http://127.0.0.1:3000/add?
name=${encodeURIComponent(item.name)}&
is_metric=${item.is_metric}&
size=${item.size}&
loc_shelf=${item.loc_shelf}&
loc_rack=${item.loc_rack}&
loc_box=${item.loc_box}&
loc_row=${item.loc_row}&
loc_col=${item.loc_col}&
loc_depth=${item.loc_depth}&
num=${item.count}&
threshold=${item.threshold}&
token=${this.authService.getToken()}`;
    return this.http.get(url);
  }
  decrementItem(item: ItemData, toChange: number): Observable<any> {
    const token = this.authService.getToken();
    const url = `http://127.0.0.1:3000/decrement?name=${encodeURIComponent(item.name)}&is_metric=${item.is_metric}&size=${item.size}&num=${toChange}&token=${token}`;
    return this.http.get(url);
  }
  incrementItem(item: ItemData, toChange: number): Observable<any> {
    const token = this.authService.getToken();
    const url = `http://127.0.0.1:3000/increment?name=${encodeURIComponent(item.name)}&is_metric=${item.is_metric}&size=${item.size}&num=${toChange}&token=${token}`;
    return this.http.get(url);
  }
}

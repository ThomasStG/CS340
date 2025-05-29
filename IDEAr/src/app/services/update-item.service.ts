import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Subject, Observable, tap } from 'rxjs';
import { ItemData } from '../item-data';
import { AuthService } from './auth.service';
import { HttpParams } from '@angular/common/http';

@Injectable({
  providedIn: 'root',
})
export class UpdateItemService {
  private signalSource = new Subject<any>();

  signal$ = this.signalSource.asObservable();
  sendSignal(data: any) {
    this.signalSource.next(data);
  }

  constructor(
    private http: HttpClient,
    private authService: AuthService,
  ) {}
  updateItem(oldItem: ItemData, newItem: ItemData): Observable<any> {
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
    return this.http.get(url).pipe(tap(() => this.sendSignal('refresh Items')));
    /*
     * updates item, can update: name, metric status, size, id, location, count
     *
     * Args:
     *   name, metric, size
     *
     * Returns:
     *
     */
  }
  deleteItem(item: ItemData): Observable<any> {
    const url = `http://127.0.0.1:3000/remove?name=${encodeURIComponent(item.name)}&is_metric=${item.is_metric}&size=${item.size}&token=${this.authService.getToken()}`;
    return this.http.get(url).pipe(tap(() => this.sendSignal('refresh Items')));
    /*
     * gets item and deletes it
     *
     * Args:
     *   itemData
     *
     * Returns:
     *
     */
  }

  addItem(item: ItemData): Observable<any> {
    const params = new HttpParams()
      .set('name', item.name)
      .set('is_metric', item.is_metric ? '1' : '0') // Ensure it's '1' or '0'
      .set('size', item.size)
      .set('loc_shelf', item.loc_shelf)
      .set('loc_rack', item.loc_rack)
      .set('loc_box', item.loc_box)
      .set('loc_row', item.loc_row)
      .set('loc_col', item.loc_col)
      .set('loc_depth', item.loc_depth)
      .set('num', item.count.toString())
      .set('threshold', item.threshold.toString())
      .set('token', this.authService.getToken());

    const url = 'http://127.0.0.1:3000/addItem';
    return this.http
      .get(url, { params })
      .pipe(tap(() => this.sendSignal('refresh Items')));
    /*
     * adds item to dataset
     *
     * Args:
     *   ItemData
     *
     * Returns:
     *   a new item for the lst
     */
  }
  decrementItem(item: ItemData, toChange: number): Observable<any> {
    const token = this.authService.getToken();
    const url = `http://127.0.0.1:3000/decrement?name=${encodeURIComponent(item.name)}&is_metric=${item.is_metric}&size=${item.size}&num=${toChange}&token=${token}`;
    return this.http.get(url);
    /*
     * decrements item
     *
     * Args:
     *   ItemData, number
     *
     * Returns:
     *
     */
  }
  incrementItem(item: ItemData, toChange: number): Observable<any> {
    const token = this.authService.getToken();
    const url = `http://127.0.0.1:3000/increment?name=${encodeURIComponent(item.name)}&is_metric=${item.is_metric}&size=${item.size}&num=${toChange}&token=${token}`;
    return this.http.get(url);
    /*
     * increments item
     *
     * Args:
     *   ItemData, number
     *
     * Returns:
     *
     */
  }
}

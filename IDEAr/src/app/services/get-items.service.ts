import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root',
})
export class GetItemsService {
  constructor(private http: HttpClient) {/*
     * constructor
     *
     * Args:
     *  private http client
     *
     * Returns:
     *   nothin'
     */}

  getItem(name: string, isMetric: boolean, size: string): Observable<any> {
    const url = `http://127.0.0.1:3000/find?name=${encodeURIComponent(name)}&is_metric=${isMetric}&size=${size}`;
    return this.http.get(url);
    /*
     * gets item searched for
     *
     * Args:
     *   anme, metric, size
     *
     * Returns:
     *   the specified item
     */
  }
  getFuzzyItems(
    name: string,
    isMetric: boolean,
    size: string,
  ): Observable<any> {
    const url = `http://127.0.0.1:3000/fuzzyfind?name=${encodeURIComponent(name)}&is_metric=${isMetric}&size=${size}`;
    return this.http.get(url);
    /*
     * gets item similar to searched for if it cant get the item
     *
     * Args:
     *   anme, metric, size
     *
     * Returns:
     *   similar item
     */
  }
  getAllItems(): Observable<any> {
    const url = 'http://127.0.0.1:3000/findAll';
    return this.http.get(url);
    /*
     * finds all items
     *
     * Args:
     *   None
     *
     * Returns:
     *   
     */
  }
}

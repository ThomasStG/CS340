import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root',
})
export class GetItemsService {
  constructor(private http: HttpClient) {}

//functions requesting data passed from the front end to the backend (ts files). Then, this connects to the API. 

  addItem(name: string, isMetric: boolean, size: string, location: string, threshold: number, isContacted: boolean ): Observable<any> {
    const url = `http://127.0.0.1:3000/add?name=${encodeURIComponent(name)}&isMetric=${isMetric}&size=${size}&location=${location}&threshold=${threshold}&isContacted=${isContacted}`;
    return this.http.get(url); 
  }
  removeItem(name: string, isMetric: boolean, size: string): Observable<any> {
    const url = `http://127.0.0.1:3000/remove?name=${encodeURIComponent(name)}&isMetric=${isMetric}&size=${size}`;
    return this.http.get(url);
  }
  incrementItem(name:string, isMetric: boolean, size: string): Observable<any> {
    const url = `http://127.0.0.1:3000/increment?name=${encodeURIComponent(name)}&isMetric=${isMetric}&size=${size}`;
    return this.http.get(url);

  }
  decrementItem(name:string, isMetric: boolean, size: string): Observable<any> {
    const url = `http://127.0.0.1.3000/decrement?name=${encodeURIComponent(name)}&isMetric=${isMetric}&size=${size}`;
    return this.http.get(url);
  }

    
  findByName(name: string): Observable<any> {
    const url = `http://127.0.0.1:3000/findByName?name=${encodeURIComponent(name)}`;
    return this.http.get(url);
  }

  getItem(name: string, isMetric: boolean, size: string): Observable<any> {
    const url = `http://127.0.0.1:3000/find?name=${encodeURIComponent(name)}&is_metric=${isMetric}&size=${size}`;
    return this.http.get(url);
  }
  getFuzzyItems(
    name: string,
    isMetric: boolean,
    size: string,
  ): Observable<any> {
    const url = `http://127.0.0.1:3000/fuzzyfind?name=${encodeURIComponent(name)}&is_metric=${isMetric}&size=${size}`;
    return this.http.get(url);
  }
  getAllItems(): Observable<any> {
    const url = 'http://127.0.0.1:3000/findAll';
    
    return this.http.get(url);
  }
}

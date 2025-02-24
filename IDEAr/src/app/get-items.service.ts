import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root',
})
export class GetItemsService {
  constructor(private http: HttpClient) {}

  getData(name: string, isMetric: boolean, size: string): Observable<any> {
    const url = `http://127.0.0.1:3000/fuzzyfind?name=${encodeURIComponent(name)}&isMetric=${isMetric}&size=${size}`;
    return this.http.get(url);
  }
}

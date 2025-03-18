import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root',
})
export class UpdateItemService {
  constructor(private http: HttpClient) {}
  updateItem(
    name: string,
    isMetric: boolean,
    size: string,
    location: string,
    threshold: number,
  ): Observable<any> {
    var locationJSON = JSON.stringify(location);
    const url = `http://127.0.0.1:3000/update?name=${encodeURIComponent(name)}&isMetric=${isMetric}&size=${size}&${encodeURIComponent(locationJSON)}&${threshold}`;
    return this.http.get(url);
  }
}

import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root',
})
export class UpdateItemService {
  constructor(private http: HttpClient) {}
  updateItem(
    id: number,
    name: string,
    isMetric: boolean,
    size: string,
    location: string,
    threshold: number,
    new_name: string,
    new_size: string,
    new_isMetric: boolean,
  ): Observable<any> {
    var locationJSON = JSON.stringify(location);
    const url = `http://127.0.0.1:3000/updateitem?
                  name=${encodeURIComponent(name)}&
                  new_name=${encodeURIComponent(new_name)}&
                  isMetric=${isMetric}&
                  new_isMetric=${new_isMetric}&
                  size=${size}&
                  new_size=${new_size}&
                  id=${id}&
                  location=${encodeURIComponent(locationJSON)}&
                  threshold=${threshold}`;
    return this.http.get(url);
  }
}

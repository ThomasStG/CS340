import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { HttpClient } from '@angular/common/http';

@Injectable({
  providedIn: 'root',
})
export class ElectricalSearchService {
  constructor(private http: HttpClient) {}

  searchSimilarActive(name: string, id: number): Observable<any> {
    console.log(name, id);
    return this.http.get<any>(
      `http://localhost:3000/electricalFuzzyActive?name=${name}&part_id=${id}`,
    );
  }
  searchIdenticalActive(name: string, id: number): Observable<any> {
    return this.http.get<any>(
      `http://localhost:3000/electricalFindActive?name=${name}&id=${id}`,
    );
  }

  searchSimilarPassive(
    value: number,
    tolerance: number,
    mounting_method: string,
    item_type: string,
    search_percent: number,
  ): Observable<any> {
    console.log(value, tolerance, mounting_method, item_type, search_percent);
    return this.http.get<any>(
      `http://localhost:3000/electricalFuzzyPassive?value=${value}&tolerance=${tolerance}&mounting_method=${mounting_method}&item_type=${item_type}&search_percent=${search_percent}`,
    );
  }
  searchIdenticalPassive(type: string, value: number): Observable<any> {
    return this.http.get<any>(
      `http://localhost:3000/electricalFindPassive?item_type=${type}&value=${value}`,
    );
  }
  searchSimilarAssembly(
    type: string,
    name: string,
    id: number,
  ): Observable<any> {
    return this.http.get<any>(
      `http://localhost:3000/electricalFuzzyAssembly?subtype=${type}&name=${name}&id=${id}`,
    );
  }
  searchIdenticalAssembly(
    type: string,
    name: string,
    id: number,
  ): Observable<any> {
    return this.http.get<any>(
      `http://localhost:3000/electricalFindAssembly?subtype=${type}&name=${name}&id=${id}`,
    );
  }

  searchThreshold(data: any): Observable<any> {
    return this.http.post<any>(
      'http://localhost:3000/electricalFindBelowThreshold',
      data,
    );
  }
}

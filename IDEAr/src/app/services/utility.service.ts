import { Injectable } from '@angular/core';
import { CookieService } from 'ngx-cookie-service';
import { HttpClient } from '@angular/common/http';
import { Observable, map } from 'rxjs';

@Injectable({
  providedIn: 'root',
})
export class UtilityService {
  private dayNight: string = 'day_night';
  constructor(
    private http: HttpClient,
    private cookieService: CookieService,
  ) {}

  setMode(val: boolean): void {
    this.cookieService.set(this.dayNight, val.toString());
  }

  isDarkMode(): boolean {
    const cookie = this.cookieService.get(this.dayNight);
    return cookie.toLowerCase() == 'true';
  }

  loadFile(file: string): void {
    this.http
      .get(`http://127.0.0.1:3000/restoreDatabase?file=${file}`)
      .subscribe();
  }
  getFiles(): Observable<string[]> {
    // Check if the response is an object and contains the expected data field
    return this.http
      .get<{ files: string[] }>('http://127.0.0.1:3000/getFiles')
      .pipe(
        map((response) => response.files), // Extract 'data' field from the response
      );
  }

  backupDatabase(): void {
    this.http.get('http://127.0.0.1:3000/backupDatabase').subscribe({
      next: (response) => {
        // Optionally, notify the user with a success message (e.g., Toast, alert)
      },
      error: (error) => {
        console.error('Error during database backup:', error);
        // Optionally, notify the user with an error message
      },
    });
  }
  uploadFile(file: any): Observable<any> {
    const formData = new FormData();
    formData.append('file', file);
    return this.http.post('http://127.0.0.1:3000/uploadFile', formData);
  }
  appendFile(file: any): Observable<any> {
    const formData = new FormData();
    formData.append('file', file);
    return this.http.post('http://127.0.0.1:3000/appendFile', formData);
  }
  downloadFile(fileUrl: string): Observable<Blob> {
    return this.http.get(
      `http://127.0.0.1:3000/downloadFile?fileName=${encodeURIComponent(fileUrl)}`,
      { responseType: 'blob' },
    );
  }
  getLogFiles(): Observable<string> {
    return this.http.get<{ log: string }>('http://127.0.0.1:3000/get_log').pipe(
      map((response) => response.log), // Extract 'data' field from the response
    );
  }
  getElectricalTooltip(): Observable<string> {
    return this.http
      .get<{ tooltip: string }>('http://127.0.0.1:3000/getElectricalTooltip')
      .pipe(
        map((response) => response.tooltip), // Extract 'data' field from the response
      );
  }

  setElectricalTooltip(tooltip: string): Observable<string> {
    return this.http
      .post<{
        tooltip: string;
      }>(`http://127.0.0.1:3000/setElectricalTooltip`, { tooltip })
      .pipe(
        map((response) => response.tooltip), // Extract 'data' field from the response);
      );
  }

  setElectricalMultiplier(): Observable<string> {
    return this.http
      .get<{
        message: string;
      }>(`http://127.0.0.1:3000/updateMultipliers`)
      .pipe(map((response) => response.message)); // Extract 'data' field from the response
  }

  getElectricalMultiplier(): Observable<
    { type: string; multiplier: string[]; values: number[] }[]
  > {
    return this.http
      .get<{
        multiplier: { type: string; multiplier: string[]; values: number[] }[];
      }>('http://127.0.0.1:3000/getMultipliers')
      .pipe(
        map((response) => response.multiplier), // ? return just the array
      );
  }
  getElectricalFiles(): Observable<string[]> {
    // Check if the response is an object and contains the expected data field
    return this.http
      .get<{ files: string[] }>('http://127.0.0.1:3000/getElectricalFiles')
      .pipe(
        map((response) => response.files), // Extract 'data' field from the response
      );
  }
  loadFileElectrical(file: string): void {
    this.http
      .get(`http://127.0.0.1:3000/restoreDatabaseElectrical?file=${file}`)
      .subscribe();
  }
  backupDatabaseElectrical(): Observable<any> {
    return this.http
      .get('http://127.0.0.1:3000/backupDatabaseElectrical')
      .pipe(map((response) => response));
  }
  appendFileElectrical(file: any): Observable<any> {
    const formData = new FormData();
    formData.append('file', file);
    return this.http.post(
      'http://127.0.0.1:3000/appendFileElectrical',
      formData,
    );
  }
}

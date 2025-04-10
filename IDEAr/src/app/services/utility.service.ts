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
}

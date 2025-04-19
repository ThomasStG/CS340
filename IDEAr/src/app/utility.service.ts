import { Injectable } from '@angular/core';
import { CookieService } from 'ngx-cookie-service';

@Injectable({
  providedIn: 'root',
})
export class UtilityService {
  private dayNight: string = 'day_night';
  constructor(private cookieService: CookieService) {}

  setMode(val: boolean): void {
    this.cookieService.set(this.dayNight, val.toString());
  }

  isDarkMode(): boolean {
    const cookie = this.cookieService.get(this.dayNight);
    return cookie.toLowerCase() == 'true';
  }
}

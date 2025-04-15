import { Component } from '@angular/core';
import { AuthService } from './services/auth.service';
import { OnInit } from '@angular/core';
import { UtilityService } from './services/utility.service';
import { BehaviorSubject } from 'rxjs';
import { ChangeDetectorRef } from '@angular/core';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrl: './app.component.css',
})
export class AppComponent implements OnInit {
  title = 'IDEAr';
  darkMode = new BehaviorSubject<boolean>(false);

  constructor(
    public authService: AuthService,
    public utilityService: UtilityService,
    private cdr: ChangeDetectorRef
  ) {}
  logout() {
    this.authService.logout();
  }

  setMode(val: boolean) {
    this.utilityService.setMode(val);
    this.darkMode.next(val);
    this.cdr.detectChanges();
  }

  ngOnInit() {
    this.darkMode.next(this.utilityService.isDarkMode());
  }
}
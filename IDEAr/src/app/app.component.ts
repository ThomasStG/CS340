import { Component } from '@angular/core';
import { AuthService } from './auth.service';
import { UtilityService } from './utility.service';
import { BehaviorSubject } from 'rxjs';
import { OnInit } from '@angular/core';

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
  ) {}
  logout() {
    this.authService.logout();
  }

  setMode(val: boolean) {
    console.log('Button clicked, setting mode to:', val);
    this.utilityService.setMode(val);
    this.darkMode.next(val);
    console.log('BehaviorSubject new value:', this.darkMode.value);
  }

  ngOnInit() {
    this.darkMode.next(this.utilityService.isDarkMode());
  }
}

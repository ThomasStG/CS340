import { Component } from '@angular/core';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  standalone: false,
  styleUrl: './app.component.css',
})
export class AppComponent {
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
    this.utilityService.setMode(val);
    this.darkMode.next(val);
  }

  ngOnInit() {
    this.darkMode.next(this.utilityService.isDarkMode());
  }
}

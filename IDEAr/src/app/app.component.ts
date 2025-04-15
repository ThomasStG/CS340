import { ViewChild, Component, ElementRef, HostListener } from '@angular/core';
import { AuthService } from './services/auth.service';
import { OnInit } from '@angular/core';
import { UtilityService } from './services/utility.service';
import { BehaviorSubject } from 'rxjs';

import { Inject, PLATFORM_ID } from '@angular/core';
import { isPlatformBrowser } from '@angular/common';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrl: './app.component.css',
})
export class AppComponent implements OnInit {
  title = 'IDEAr';
  darkMode = new BehaviorSubject<boolean>(true);
  showHomeDropdown = false;
  showAdminDropdown = false;
  showManagementDropdown = false;
  isAuthenticated = false;
  private isBrowser: boolean;
  @ViewChild('homeDropdownRef') homeDropdownRef!: ElementRef;
  @ViewChild('adminDropdownRef') adminDropdownRef!: ElementRef;
  @ViewChild('managementDropdownRef') managementDropdownRef!: ElementRef;

  constructor(
    public authService: AuthService,
    public utilityService: UtilityService,
    private eRef: ElementRef,
    @Inject(PLATFORM_ID) private platformId: Object,
  ) {
    this.isBrowser = isPlatformBrowser(this.platformId);
  }

  @HostListener('document:click', ['$event'])
  clickOutside(event: MouseEvent) {
    if (!this.isBrowser) return;

    const target = event.target as HTMLElement;

    const clickedInsideHome =
      this.homeDropdownRef?.nativeElement.contains(target);
    const clickedInsideAdmin =
      this.adminDropdownRef?.nativeElement.contains(target);
    const clickedInsideManagement =
      this.managementDropdownRef?.nativeElement.contains(target);

    if (!clickedInsideHome) this.showHomeDropdown = false;
    if (!clickedInsideAdmin) this.showAdminDropdown = false;
    if (!clickedInsideManagement) this.showManagementDropdown = false;
  }
  logout() {
    this.authService.logout();
    this.isAuthenticated = false;
  }

  setMode(val: boolean) {
    this.utilityService.setMode(val);
    this.darkMode.next(val);
  }

  ngOnInit() {
    this.darkMode.next(this.utilityService.isDarkMode());
    this.authService.authState$.subscribe((isAuthed) => {
      if (isAuthed) {
        this.onAuthSuccess();
      }
    });
  }
  toggleDarkMode() {
    this.setMode(!this.darkMode.value);
  }

  toggleDropdown(name: 'home' | 'admin' | 'management') {
    this.showHomeDropdown = name === 'home' ? !this.showHomeDropdown : false;
    this.showAdminDropdown = name === 'admin' ? !this.showAdminDropdown : false;
    this.showManagementDropdown =
      name === 'management' ? !this.showManagementDropdown : false;
  }
  onAuthSuccess() {
    this.isAuthenticated = true;
  }
}

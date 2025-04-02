import { Component } from '@angular/core';
import { AuthService } from './auth.service';
import {OnInit } from '@angular/core';
import { UtilityService } from './utility.service';
import { BehaviorSubject } from 'rxjs';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrl: './app.component.css',
})
export class AppComponent implements OnInit{
  title = 'IDEAr';
  darkMode = new BehaviorSubject<boolean>(false);


  constructor(public authService: AuthService, public utilityService:UtilityService) {}
  logout() {
    this.authService.logout();
  }

  setMode(val:boolean){
    this.utilityService.setMode(val);
    this.darkMode.next(val);
  }

  ngOnInit(){
    this.darkMode.next(this.utilityService.isDarkMode());
  } 
}


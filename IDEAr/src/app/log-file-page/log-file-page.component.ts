import { Component } from '@angular/core';
import { OnInit } from '@angular/core';
import { UtilityService } from '../services/utility.service';
import { saveAs } from 'file-saver';
import { AuthService } from '../services/auth.service';

@Component({
  selector: 'app-log-file-page',
  templateUrl: './log-file-page.component.html',
  styleUrl: './log-file-page.component.css',
})
export class LogFilePageComponent implements OnInit {
  log_data: string = '';
  constructor(private utilityService: UtilityService, private authService: AuthService) {}
  ngOnInit(): void {
    console.log('in data download');
    this.utilityService.getLogFiles().subscribe((response: string) => {
      this.log_data = response;
    });
  }
  downloadFile(event: Event): void {
    event.stopPropagation();
    const blob = new Blob([this.log_data], {
      type: 'text/plain;charset=utf-8',
    });
    saveAs(blob, 'log.txt');
  }
  check_level() {
    const level = this.authService.levelGetter().subscribe((level) => {
      if (level != 2) return true;
      else return false;
    });
  }
}

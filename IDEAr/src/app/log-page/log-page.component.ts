import { Component } from '@angular/core';
import { OnInit } from '@angular/core';
import { UtilityService } from '../services/utility.service';
import { saveAs } from 'file-saver';

@Component({
  selector: 'app-log-page',
  templateUrl: './log-page.component.html',
  styleUrl: './log-page.component.css',
})
export class LogPageComponent implements OnInit {
  log_data: string = '';
  constructor(private utilityService: UtilityService) {}
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
}

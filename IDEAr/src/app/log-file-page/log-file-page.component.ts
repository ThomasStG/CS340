import { Component } from '@angular/core';
import { OnInit } from '@angular/core';
import { UtilityService } from '../services/utility.service';
import { saveAs } from 'file-saver';
import { AuthService } from '../services/auth.service';
import { Router } from '@angular/router';

@Component({
  selector: 'app-log-file-page',
  templateUrl: './log-file-page.component.html',
  styleUrl: './log-file-page.component.css',
})
export class LogFilePageComponent implements OnInit {
  log_data: string = '';
  constructor(
    private utilityService: UtilityService,
    private authService: AuthService,
    private router: Router,
  ) {}
  ngOnInit(): void {
    this.authService.getAuthLevel().subscribe((level) => {
      if (level == 0) {
        this.utilityService.getLogFiles().subscribe((response: string) => {
          this.log_data = response;
        });
      } else {
        this.router.navigate(['/authentication']);
      }
    });
    /*
     * Runs on component initialization. Checks if the user is authenticated and level 0.  if not, navigates to the authentication page,
     * otherwise load the item list and subscribe to a signal to refresh items on update.
     *
     * Args:
     *   None
     *
     * Returns:
     *   None
     */
  }
  downloadFile(event: Event): void {
    event.stopPropagation();
    const blob = new Blob([this.log_data], {
      type: 'text/plain;charset=utf-8',
    });
    saveAs(blob, 'log.txt');
    /*
     * downloads a file, converts file into plaintext (readable stuffs) and saves it to computer as log.txt
     *
     * Args:
     *   Event
     *
     * Returns:
     *   None
     */
  }
  check_level() {
    const level = this.authService.levelGetter().subscribe((level) => {
      if (level != 2) return true;
      else return false;
    });
    /*
     *  Checks if the user has permission to acesss this feature, if they are not 2 return false, else true
     *
     * Args:
     *   None
     *
     * Returns:
     *   bool true/false
     */
  }
}

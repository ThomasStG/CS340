import { Component } from '@angular/core';
import { OnInit } from '@angular/core';
import { AuthService } from '../services/auth.service';
import { UserData } from '../user-data';
import { FormControl, FormGroup } from '@angular/forms';
import { MatDialog } from '@angular/material/dialog';
import { ConfirmationPopupComponent } from '../confirmation-popup/confirmation-popup.component';
import { Observable } from 'rxjs';
import { filter } from 'rxjs/operators';
import { Router } from '@angular/router';

@Component({
  selector: 'app-user-management',
  templateUrl: './user-management.component.html',
  styleUrl: './user-management.component.css',
})
export class UserManagementComponent implements OnInit {
  users: UserData[] = [];

  newUserForm = new FormGroup({
    username: new FormControl(''),
    password: new FormControl(''),
    level: new FormControl('2'),
  });

  level$ = this.authService
    .levelGetter()
    .pipe(
      filter((level): level is number => level !== null),
    ) as Observable<number>;

  constructor(
    private authService: AuthService,
    private router: Router,
    public dialog: MatDialog,
  ) {}

  ngOnInit(): void {
    this.authService.getAuthLevel().subscribe((level) => {
      if (level == 0) {
        this.authService.getUsers().subscribe((response: UserData[]) => {
          this.users = response;
        });
      } else {
        this.router.navigate(['/authentication']);
      }
    });
  }
  onCreate() {
    const formData = this.newUserForm.value;

    if (
      formData.username &&
      formData.password &&
      formData.level !== null &&
      formData.level !== undefined
    ) {
      const data: UserData = {
        username: formData.username,
        level: Number(formData.level), // ensure it's a number
      };
      const pass = formData.password as string;
      this.authService.createUser(data, pass).subscribe({
        next: () => {
          // After creating the user, fetch the updated list of users
          this.authService.getUsers().subscribe((response: UserData[]) => {
            this.users = response; // Update users array with the new data
          });
        },
        error: (error) => {
          // Handle the error if the user creation fails
          console.error('User creation failed:', error);
        },
      });

      // Reset the form after submitting
      this.newUserForm.reset();
    } else {
    }
  }

  confirmPopup(value: string) {
    const ConfirmationPopUp = this.dialog.open(ConfirmationPopupComponent);
    ConfirmationPopUp.afterOpened().subscribe(() => {
      ConfirmationPopUp.componentInstance.updatePopup(value);
    });

    ConfirmationPopUp.afterClosed().subscribe((result: boolean) => {
      if (result === true && value === 'create') {
        this.onCreate();
      }
    });
  }
  onUserListUpdated(updatedUsers: UserData[]) {
    this.users = updatedUsers;
  }
  check_level() {
    const level = this.authService.levelGetter().subscribe((level) => {
      if (level == 0) return true;
      else return false;
    });
  }
}

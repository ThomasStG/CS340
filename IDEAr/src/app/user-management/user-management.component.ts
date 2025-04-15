import { Component } from '@angular/core';
import { OnInit } from '@angular/core';
import { AuthService } from '../services/auth.service';
import { UserData } from '../user-data';
import { FormControl, FormGroup } from '@angular/forms';
import { MatDialog } from '@angular/material/dialog';
import { ConfirmationPopupComponent } from '../confirmation-popup/confirmation-popup.component';


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

  constructor(
    private authService: AuthService,
    public dialog: MatDialog,

  ) {}

  ngOnInit(): void {
    this.authService.getUsers().subscribe((response: UserData[]) => {
      this.users = response;
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
      this.authService.createUser(data, pass).subscribe();
      this.authService.getUsers().subscribe((response: UserData[]) => {
        this.users = response;
      });
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
}

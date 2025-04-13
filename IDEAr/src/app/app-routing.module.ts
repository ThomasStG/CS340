import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';

import { AdminComponent } from './admin/admin.component';
import { AuthenticationComponent } from './authentication/authentication.component';
import { DataDownloadComponent } from './data-download/data-download.component';
import { ElectricalHomeComponent } from './electrical-home/electrical-home.component';
import { HomeComponent } from './home/home.component';
import { LogFilePageComponent } from './log-file-page/log-file-page.component';
import { UserManagementComponent } from './user-management/user-management.component';

const routes: Routes = [
  { path: '', component: HomeComponent }, // Home Page
  { path: 'admin', component: AdminComponent }, // Admin Page
  { path: 'authentication', component: AuthenticationComponent },
  { path: 'data-download', component: DataDownloadComponent },
  { path: 'logs', component: LogFilePageComponent },
  { path: 'electrical-home', component: ElectricalHomeComponent },
  { path: 'user-management', component: UserManagementComponent },
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule],
})
export class AppRoutingModule {}

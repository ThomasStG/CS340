import { NgModule } from '@angular/core';
import {
  BrowserModule,
  provideClientHydration,
} from '@angular/platform-browser';
import { HttpClientModule } from '@angular/common/http';
import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { ItemDescriptionComponent } from './item-description/item-description.component';
import { ItemComponent } from './item/item.component';
import { ItemSearchComponent } from './item-search/item-search.component';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { HomeComponent } from './home/home.component';
import { AdminComponent } from './admin/admin.component';
import { RouterModule, Routes } from '@angular/router';
import { AuthenticationComponent } from './authentication/authentication.component';
import { AdminItemComponent } from './admin-item/admin-item.component';
import { AdminPopupComponent } from './admin-popup/admin-popup.component';
import { MatDialogModule } from '@angular/material/dialog';
import { DataDownloadComponent } from './data-download/data-download.component';
import { ItemPopupComponent } from './item-popup/item-popup.component';
import { ElectricalHomeComponent } from './electrical-home/electrical-home.component';
import { ElectricalItemSearchComponent } from './electrical-item-search/electrical-item-search.component';
import { LogFilePageComponent } from './log-file-page/log-file-page.component';
import { UserManagementComponent } from './user-management/user-management.component';
import { UserComponent } from './user/user.component';
import { ElectricalItemPopupComponent } from './electrical-item-popup/electrical-item-popup.component';
import { ElectricalAdminComponent } from './electrical-admin/electrical-admin.component';
import { ElectricalAdminPopupComponent } from './electrical-admin-popup/electrical-admin-popup.component';
import { ElectricalAdminSearchComponent } from './electrical-admin-search/electrical-admin-search.component';
import { DataDownloadElectricalComponent } from './data-download-electrical/data-download-electrical.component';

@NgModule({
  declarations: [
    AppComponent,
    ItemDescriptionComponent,
    ItemComponent,
    ItemSearchComponent,
    HomeComponent,
    AdminComponent,
    AuthenticationComponent,
    AdminItemComponent,
    AdminPopupComponent,
    DataDownloadComponent,
    ItemPopupComponent,
    LogFilePageComponent,
    ElectricalHomeComponent,
    UserManagementComponent,
    UserComponent,
    ElectricalItemSearchComponent,
    ElectricalItemPopupComponent,
    ElectricalAdminComponent,
    ElectricalAdminPopupComponent,
    ElectricalAdminSearchComponent,
    DataDownloadElectricalComponent,
  ],
  imports: [
    ReactiveFormsModule,
    BrowserModule,
    AppRoutingModule,
    FormsModule,
    HttpClientModule,
    RouterModule,
  ],
  exports: [RouterModule],
  providers: [provideClientHydration()],
  bootstrap: [AppComponent],
})
export class AppModule {}

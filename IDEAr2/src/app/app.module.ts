import { NgModule } from '@angular/core';
import {
  BrowserModule,
  provideClientHydration,
  withEventReplay,
} from '@angular/platform-browser';

import { AppRoutingModule } from './app-routing.module';
import { HttpClientModule } from '@angular/common/http';
import { AppComponent } from './app.component';
import { AdminComponent } from './admin/admin.component';
import { AdminItemComponent } from './admin-item/admin-item.component';
import { AdminPopupComponent } from './admin-popup/admin-popup.component';
import { AuthenticationComponent } from './authentication/authentication.component';
import { DataDownloadComponent } from './data-download/data-download.component';
import { ElectricalHomeComponent } from './electrical-home/electrical-home.component';
import { HomeComponent } from './home/home.component';
import { ItemComponent } from './item/item.component';
import { ItemPopupComponent } from './item-popup/item-popup.component';
import { ItemSearchComponent } from './item-search/item-search.component';
import { LogPageComponent } from './log-page/log-page.component';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { RouterModule, Routes } from '@angular/router';
import { MatDialogModule } from '@angular/material/dialog';

const routes: Routes = [
  { path: '', component: HomeComponent }, // Home Page
  { path: 'admin', component: AdminComponent }, // Admin Page
  { path: 'authentication', component: AuthenticationComponent },
  { path: 'data-download', component: DataDownloadComponent },
  { path: 'logs', component: LogsComponent },
  { path: 'electrical-home', component: ElectricalHomeComponent },
];

@NgModule({
  declarations: [
    AppComponent,
    AdminComponent,
    AdminIemComponent,
    AdminItemComponent,
    AdminPopupComponent,
    AuthenticationComponent,
    DataDownloadComponent,
    ElectricalHomeComponent,
    HomeComponent,
    ItemComponent,
    ItemPopupComponent,
    ItemSearchComponent,
    LogPageComponent,
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    HttpClientModule,
    FormsModule,
    ReactiveFormsModule,
    RouterModule,
    MatDialogModule,
  ],
  providers: [provideClientHydration(withEventReplay())],
  bootstrap: [AppComponent],
})
export class AppModule {}

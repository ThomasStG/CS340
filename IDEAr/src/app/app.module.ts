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
import { LogsComponent } from './logs/logs.component';
import { ElectricalHomeComponent } from './electrical-home/electrical-home.component';

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
    LogsComponent,
    ElectricalHomeComponent,
  ],
  imports: [
    ReactiveFormsModule,
    BrowserModule,
    AppRoutingModule,
    FormsModule,
    HttpClientModule,
    RouterModule.forRoot(routes),
  ],
  exports: [RouterModule],
  providers: [provideClientHydration()],
  bootstrap: [AppComponent],
})
export class AppModule {}
